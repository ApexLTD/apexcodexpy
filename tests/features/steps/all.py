from behave.runner import Context
from behave import given, use_step_matcher, then, when


@given("nothing")
def step_impl(context: Context):
    pass


@when("{} do what {} have always done,")
def _(context: Context, _: str, __: str):
    pass


@then("{} get what {} have always got!")
def _(context: Context, _: str, __: str):
    pass
