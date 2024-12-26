from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    try:
        # تأكد أن القيم أرقام
        value = int(value)
        arg = int(arg)
        return value * arg
    except (ValueError, TypeError):
        return 0  # إعادة 0 إذا كانت القيم غير صالحة
