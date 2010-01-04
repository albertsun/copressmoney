from django.db import models

# Fundamental model is for a single line of the ledger. Additional model defines a basic client. Optional foreign key associates ledger line to client.

class Client(models.Model):
    """Identifies a Client that will have LedgerLines associated with them. A Client can be any entity with whom money changes hands, including suppliers, employees, etc. Only a bare minimum of information is kept."""
    name = models.CharField(max_length=64)
    mail = models.EmailField()
    site = models.URLField(verify_exists=False)
    description = models.TextField()

class LedgerLine(models.Model):
    """A single line of a double entry ledger, tracking the balances of seven accounts."""

    #identifiers
    date = models.DateField()
    client = models.ForeignKey(Client, null=True)
    title = models.CharField(max_length=128)
    description = models.TextField()
    documentation = models.URLField(verify_exists=False)
    category = models.CharField(max_length=64)
    
    #ledger balance changes
    revenue = models.DecimalField(max_digits=14, decimal_places=5)
    expenses = models.DecimalField(max_digits=14, decimal_places=5)
    cash = models.DecimalField(max_digits=14, decimal_places=5)
    unearned = models.DecimalField(max_digits=14, decimal_places=5)
    prepaid = models.DecimalField(max_digits=14, decimal_places=5)
    acctsreceivable = models.DecimalField(max_digits=14, decimal_places=5)
    acctspayable = models.DecimalField(max_digits=14, decimal_places=5)
