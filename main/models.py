from django.db import models


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Study(models.Model):
    study_number = models.IntegerField(unique=True)
    study_name = models.CharField(max_length=255, unique=True)
    missing = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.study_number} ({self.study_name})"

    class Meta:
        verbose_name_plural = "studies"
        ordering = ["study_number"]

class Group(models.Model):
    group_number = models.IntegerField(unique=True)
    group_name = models.CharField(max_length=255, unique=True)
    missing = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.group_number} ({self.group_name})"

    class Meta:
        ordering = ["group_number"]


class Instrument(models.Model):
    instrument_name = models.CharField(max_length=255, unique=True)
    # optionally include the label - i.e. the REDCap display name
    instrument_label = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.instrument_name

    class Meta:
        ordering = ["instrument_name"]

class StudyInstrument(models.Model):
    study = models.ForeignKey("Study", on_delete=models.CASCADE)
    instrument = models.ForeignKey("Instrument", on_delete=models.CASCADE)
    min_age = models.FloatField(blank=True, null=True, help_text="Leave blank for no min age")
    max_age = models.FloatField(blank=True, null=True, help_text="Leave blank for no max age")

class InstrumentCreationRule(models.Model):
    study = models.ForeignKey("Study", on_delete=models.CASCADE)
    group = models.ForeignKey("Group", on_delete=models.PROTECT, blank=True, null=True, help_text="Leave blank for all groups")
    min_age = models.FloatField(blank=True, null=True, help_text="Leave blank for no min age")
    max_age = models.FloatField(blank=True, null=True, help_text="Leave blank for no max age")
    instruments = models.ManyToManyField("Instrument", blank=True, help_text="Hold ctrl to select multiple")

    def __str__(self):
        return f"rule #{self.id} - study: {self.study}"

    class Meta:
        ordering = ["study__study_name", "id"]

    def list_instruments(self):
        list = []
        for oInstrument in self.instruments.all():
            list.append(oInstrument.instrument_name)
        return ", ".join(list)

    def describe_rule(self):
        group_desc = ""
        min_age_desc = ""
        max_age_desc = ""
        if self.group:
            group_desc = f" and group is {self.group}"
        if self.min_age:
            min_age_desc = f" and age >= {self.min_age}"
        if self.max_age:
            max_age_desc = f" and age <= {self.max_age}"
        desc = f"if study is {self.study}{group_desc}{min_age_desc}{max_age_desc}"
        return desc







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

