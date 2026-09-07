from django import template

register = template.Library()

@register.filter
def get_sweeping_slots(street, day):
    mapping = {
        'monday': street.monday_sweeping_time_slots,
        'tuesday': street.tuesday_sweeping_time_slots,
        'wednesday': street.wednesday_sweeping_time_slots,
        'thursday': street.thursday_sweeping_time_slots,
        'friday': street.friday_sweeping_time_slots,
        'saturday': street.saturday_sweeping_time_slots,
        'sunday': street.sunday_sweeping_time_slots,
    }
    return mapping.get(day) or []

@register.filter
def get_solid_waste_slots(street, day):
    mapping = {
        'monday': street.monday_solid_waste_time_slots,
        'tuesday': street.tuesday_solid_waste_time_slots,
        'wednesday': street.wednesday_solid_waste_time_slots,
        'thursday': street.thursday_solid_waste_time_slots,
        'friday': street.friday_solid_waste_time_slots,
        'saturday': street.saturday_solid_waste_time_slots,
        'sunday': street.sunday_solid_waste_time_slots,
    }
    return mapping.get(day) or []
