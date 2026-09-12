from sqlalchemy import select, inspect


async def get_or_create(session, model, get_args, create_args):
    instance_by_select = await session.execute(select(model).filter_by(**get_args))
    if instance := instance_by_select.scalars().first():
        return instance
    else:
        instance = model(**create_args)
        session.add(instance)
        await session.flush()
        return instance


async def clone_instance_by_id(
    session,
    model,
    instance,
    overrides: dict | None = None,
    exclude: set[str] | None = None,
):
    excl = exclude or set()
    data = {
        c.key: getattr(instance, c.key)
        for c in inspect(model).columns
        if not c.primary_key and c.key not in excl
    }
    if overrides:
        data.update(overrides)

    clone_instance = model(**data)
    session.add(clone_instance)
    await session.flush()
    return clone_instance
