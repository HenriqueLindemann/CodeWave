from django import template

register = template.Library()

@register.simple_tag
def get_user_application(task, user):
    return task.applications.filter(developer=user).first()