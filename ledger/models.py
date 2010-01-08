from django.db import models
from django import forms
from django.forms import ModelForm

# Fundamental model is for a single line of the ledger. Additional model defines a basic client. Optional foreign key associates ledger line to client.

class Client(models.Model):
    """Identifies a Client that will have LedgerLines associated with them. A Client can be any entity with whom money changes hands, including suppliers, employees, etc. Only a bare minimum of information is kept."""
    name = models.CharField(max_length=64)
    mail = models.EmailField()
    site = models.URLField(verify_exists=False)
    description = models.TextField()

    def __unicode__(self):
        #return "<a href=\"/ledger/client/"+str(self.id)+"/\">"+self.name+"</a>"
        return self.name

class LedgerLine(models.Model):
    """A single line of a double entry ledger, tracking the balances of seven accounts."""

    #identifiers
    date = models.DateField()
    client = models.ForeignKey(Client, null=True, blank=True)
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    documentation = models.URLField(verify_exists=False, blank=True)
    category = models.CharField(max_length=64)
    
    #ledger balance changes. stored as decimal. Python objects treat them as strings.
    revenue = models.DecimalField(null=True, max_digits=14, decimal_places=5, blank=True)
    expenses = models.DecimalField(null=True, max_digits=14, decimal_places=5, blank=True)
    cash = models.DecimalField(null=True, max_digits=14, decimal_places=5, blank=True)
    unearned = models.DecimalField(null=True, max_digits=14, decimal_places=5, blank=True, verbose_name="Unearned Revenue")
    prepaid = models.DecimalField(null=True, max_digits=14, decimal_places=5, blank=True, verbose_name="Prepaid Expenses")
    acctsreceivable = models.DecimalField(null=True, max_digits=14, decimal_places=5, blank=True, verbose_name="A/R")
    acctspayable = models.DecimalField(null=True, max_digits=14, decimal_places=5, blank=True, verbose_name="A/P")

    #future additions
    #paid or unpaid (boolean)
    #related lines (many-to-many)

    def __unicode__(self):
        return str(title)+" (Entry date"+str(self.date)+")"

    class Meta:
        ordering = ['-id']

class LineForm(ModelForm):
    """Form class for the LedgerLine model."""
    description = forms.CharField(required=False, widget=forms.widgets.Textarea(attrs={'rows':4, 'cols':50}))

    class Meta:
        model = LedgerLine

