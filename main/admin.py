from django.contrib import admin

from . import models


class InstrumentCreationRuleAdmin(admin.ModelAdmin):
    list_display = ["study", "group", "min_age", "max_age", "list_instruments"]
    list_filter = ["study"]

admin.site.register(models.InstrumentCreationRule, InstrumentCreationRuleAdmin)

class StudyAdmin(admin.ModelAdmin):
    list_display = ["study_number", "study_name", "missing"]

admin.site.register(models.Study, StudyAdmin)

class GroupAdmin(admin.ModelAdmin):
    list_display = ["group_number", "group_name", "missing"]

admin.site.register(models.Group, GroupAdmin)

class InstrumentAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Instrument, InstrumentAdmin)

class CompletedVisitAdmin(admin.ModelAdmin):
    list_display = ("record_id", "instance", "created")

admin.site.register(models.CompletedVisit, CompletedVisitAdmin)

class CreatedInstrumentAdmin(admin.ModelAdmin):
   pass

admin.site.register(models.CreatedInstrument, CreatedInstrumentAdmin)
