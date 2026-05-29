from behave import given, then, when
from behave.runner import Context


@given("nothing")  # type: ignore
def step_impl(context: Context) -> None:
    pass


@when("{} do what {} have always done,")  # type: ignore
def _(context: Context, _: str, __: str) -> None:
    pass


@then("{} get what {} have always got!")  # type: ignore
def _(context: Context, _: str, __: str) -> None:
    pass
