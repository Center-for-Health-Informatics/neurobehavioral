from django.db import models


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Study(models.Model):
    study_name = models.CharField(max_length=255, unique=True)
    study_number = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.study_number}: {self.study_name}"

    class Meta:
        verbose_name_plural = "studies"

class Instrument(models.Model):
    instrument_name = models.CharField(max_length=255, unique=True)
    orig_study_field_name = models.CharField(max_length=255,
         help_text="The name of the field where the original study value should go.")
    studies_field_name = models.CharField(max_length=255,
        help_text="The name of the field where the original study value should go.")

    def __str__(self):
        return self.instrument_name

class StudyInstrument(models.Model):
    study = models.ForeignKey("Study", on_delete=models.CASCADE)
    instrument = models.ForeignKey("Instrument", on_delete=models.CASCADE)
    min_age = models.FloatField(blank=True, null=True, help_text="Leave blank for no min age")
    max_age = models.FloatField(blank=True, null=True, help_text="Leave blank for no max age")

class CompletedVisit(TimeStampedModel):
    """
    Tracks which visit records have already been processed
    """
    record_id = models.CharField(max_length=255)
    instance = models.IntegerField()

    class Meta:
        unique_together = (("record_id", "instance"),)
        ordering = ["record_id", "instance"]

    def __str__(self):
        return f"record_id {self.record_id}, instance {self.instance}"

class CreatedInstrument(models.Model):
    """
    Tracks all the instruments that were created for a visit
    """
    visit = models.ForeignKey(CompletedVisit, on_delete=models.CASCADE)
    instrument_name = models.CharField(max_length=255)
    instance = models.IntegerField()
    successful = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        response = f"record_id {self.visit.record_id}, instrument {self.instrument_name}, instance {self.instance}"
        if self.successful:
            return response
        return "(FAILED) " + response

