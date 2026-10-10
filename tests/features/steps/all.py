from behave import given, then, when
from behave.runner import Context


@given("nothing")  # type: ignore[untyped-decorator]
def step_impl(context: Context) -> None:
    pass


@when("{} do what {} have always done,")  # type: ignore[untyped-decorator]
def _(context: Context, _: str, __: str) -> None:
    pass


@then("{} get what {} have always got!")  # type: ignore[untyped-decorator]
def _(context: Context, _: str, __: str) -> None:
    pass
