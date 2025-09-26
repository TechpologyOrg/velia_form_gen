from django.db import models

class card_template(models.Model):
    name = models.CharField(max_length=255)
    organisation = models.ForeignKey('core.organisation', on_delete=models.CASCADE)
    
    # JSON data for card template structure - hierarchical array of components
    template_data = models.JSONField()
    
    # Global variables for the template
    global_vars = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class generated_card(models.Model):
    template = models.ForeignKey(card_template, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    
    # JSON data for the generated card content (populated template)
    card_data = models.JSONField()
    
    # Global variables used for this specific card instance
    global_vars = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (from {self.template.name})"