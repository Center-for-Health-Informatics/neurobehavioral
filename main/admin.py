from django.contrib import admin

from . import models


class StudyInstrumentAdmin(admin.StackedInline):
    model = models.StudyInstrument
    extra = 1

class StudyAdmin(admin.ModelAdmin):
    inlines = [StudyInstrumentAdmin]

admin.site.register(models.Study, StudyAdmin)

class InstrumentAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Instrument, InstrumentAdmin)

class CompletedVisitAdmin(admin.ModelAdmin):
    list_display = ("record_id", "instance", "created")

admin.site.register(models.CompletedVisit, CompletedVisitAdmin)

class CreatedInstrumentAdmin(admin.ModelAdmin):
   pass

admin.site.register(models.CreatedInstrument, CreatedInstrumentAdmin)
