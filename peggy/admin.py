from django.contrib import admin

from peggy.models import *


admin.site.register(Customer)
admin.site.register(Comment)
admin.site.register(Photo)
admin.site.register(SurveyResult)
admin.site.register(Article)
admin.site.register(Product)
admin.site.register(RefundClaim)

# admin.site.register(Opinion)
# admin.site.register(Choice)
#
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 3

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    # fieldsets = [
    #     (None,               {'fields': ['question']}),
    #     ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    # ]
    # list_display = ('question', 'pub_date', 'was_published_recently')
    # list_filter = ['pub_date']
    # search_fields = ['question']
    # date_hierarchy = 'pub_date'

admin.site.register(Order, OrderAdmin)
