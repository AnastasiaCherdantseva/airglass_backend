import logging
from dataclasses import dataclass
from uuid import UUID

from app.core.exceptions import ValidationError
from app.dto import CurrentUser
from app.dto.system.permission_condition import PermissionConditionAllOutPut
from app.models.system.permission_condition import ConditionType

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class JointTrigger:
    """
    Право, которое требует набор совместных прав.
    Атрибуты:
        code: Код права-триггера.
        type: Тип условия для права-триггера.
        siblings: Словарь ``код_зависимого -> тип_условия``.
            Зависимые права не имеют смысла сами по себе; они
            выдаются только вместе с триггером.
    """

    code: str
    type: ConditionType
    siblings: dict[str, ConditionType]


JOINT_TRIGGERS: list[JointTrigger] = [
    JointTrigger(
        code="USERS.CREATE",
        type=ConditionType.ROLE,
        siblings={
            "USERS.DELETE": ConditionType.CREATOR,
            "USERS.UPDATE": ConditionType.CREATOR,
            "USERS.READ": ConditionType.SUBTREE,
        },
    ),
    JointTrigger(
        code="ROLES.CREATE",
        type=ConditionType.ALL,
        siblings={
            "ROLES.DELETE": ConditionType.CREATOR,
            "ROLES.UPDATE": ConditionType.CREATOR,
            "ROLES.READ": ConditionType.CREATOR,
        },
    ),
    JointTrigger(
        code="ORGANIZATIONS.CREATE",
        type=ConditionType.ALL,
        siblings={
            "ORGANIZATIONS.DELETE": ConditionType.CREATOR,
            "ORGANIZATIONS.UPDATE": ConditionType.CREATOR,
            "ORGANIZATIONS.READ": ConditionType.CREATOR,
        },
    ),
]


# Обратный маппинг: sibling_code -> trigger.
# Используется, чтобы понять, что запрос содержит зависимое право
# без его триггера (это ошибка).
_SIBLING_TO_TRIGGER: dict[str, JointTrigger] = {
    sibling_code: trigger for trigger in JOINT_TRIGGERS for sibling_code in trigger.siblings
}


def _find_trigger(code: str, cond_type: ConditionType) -> JointTrigger | None:
    """
    Найти триггер совместных прав по коду права и типу условия.
    Args:
        code: Код права.
        cond_type: Тип условия.

    Returns:
        Подходящий триггер или ``None``, если право не является
        триггером.
    """
    return next(
        (t for t in JOINT_TRIGGERS if t.code == code and t.type == cond_type),
        None,
    )


def _find_actor_condition(
    actor: CurrentUser,
    code: str,
    cond_type: ConditionType,
) -> PermissionConditionAllOutPut | None:
    """Найти условие актора для указанного права и типа.
    Args:
        actor: Текущий пользователь.
        code: Код права.
        cond_type: Тип условия.

    Returns:
        DTO условия актора или ``None``, если не найдено.
    """
    for perm in actor.permissions:
        if perm.code != code:
            continue
        for cond in perm.conditions:
            if cond.type == cond_type:
                return cond
    return None


def build_full_conditions_package(
    *,
    actor: CurrentUser,
    requested_condition_ids: set[UUID],
) -> set[UUID]:
    """
    Собрать полный набор id условий для выдачи.

    Включает запрошенные условия и их совместные права (если триггер
    присутствует). Кидает ``ValidationError``, если зависимое право
    запрошено без триггера, или если триггер запрошен, но у актора
    нет подходящего условия для зависимого права.

    """
    # 1. Индекс условий актора: cid -> (code, cond)
    actor_conditions: dict[UUID, tuple[str, PermissionConditionAllOutPut]] = {
        cond.id: (perm.code, cond) for perm in actor.permissions for cond in perm.conditions
    }

    # 2. Проверка доступа: все запрошенные условия должны быть у актора
    foreign = requested_condition_ids - actor_conditions.keys()
    if foreign:
        logger.info(
            "build_full_conditions_package: actor (id=%s) tried to use "
            "conditions he has no access to: %s",
            actor.id,
            sorted(foreign),
        )
        raise ValidationError("Недостаточно прав: часть условий недоступна.")

    requested_ids = set(requested_condition_ids)

    # 3. Обратный маппинг: зависимые права не могут приходить без триггера
    requested_codes: set[str] = {actor_conditions[cid][0] for cid in requested_ids}
    for cid in requested_ids:
        code, cond = actor_conditions[cid]
        trigger = _find_trigger(code, cond.type)
        if trigger is not None:
            # Это триггер — ок, siblings добавим ниже
            continue
        parent = _SIBLING_TO_TRIGGER.get(code)
        if parent is None:
            # Обычное право, не триггер и не sibling — оставляем как есть
            continue
        # Это sibling: проверяем, есть ли в запросе триггер
        if parent.code not in requested_codes:
            logger.info(
                "build_full_conditions_package: actor (id=%s) requested "
                "sibling %s (%s) without trigger %s",
                actor.id,
                code,
                cond.type,
                parent.code,
            )
            raise ValidationError(
                f"Право {code} не может быть выдано отдельно. "
                f"Оно добавляется только вместе с {parent.code}."
            )

    # 4. Для каждого триггера из запроса — добавить его siblings
    extra_ids: set[UUID] = set()
    for cid in requested_ids:
        code, cond = actor_conditions[cid]
        trigger = _find_trigger(code, cond.type)
        if trigger is None:
            continue

        for sib_code, sib_type in trigger.siblings.items():
            sib_cond = _find_actor_condition(actor, sib_code, sib_type)
            if sib_cond is None:
                logger.warning(
                    "build_full_conditions_package: actor (id=%s) has "
                    "no condition %s/%s, required by trigger %s",
                    actor.id,
                    sib_code,
                    sib_type,
                    code,
                )
                raise ValidationError(
                    f"У вас нет права {sib_code} ({sib_type}), необходимого вместе с {code}."
                )
            extra_ids.add(sib_cond.id)

    return requested_ids | extra_ids
