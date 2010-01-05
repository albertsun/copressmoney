from django.db import models

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
    client = models.ForeignKey(Client, null=True)
    title = models.CharField(max_length=128)
    description = models.TextField()
    documentation = models.URLField(verify_exists=False)
    category = models.CharField(max_length=64)
    
    #ledger balance changes. stored as decimal. Python objects treat them as strings.
    revenue = models.DecimalField(null=True, max_digits=14, decimal_places=5)
    expenses = models.DecimalField(null=True, max_digits=14, decimal_places=5)
    cash = models.DecimalField(null=True, max_digits=14, decimal_places=5)
    unearned = models.DecimalField(null=True, max_digits=14, decimal_places=5)
    prepaid = models.DecimalField(null=True, max_digits=14, decimal_places=5)
    acctsreceivable = models.DecimalField(null=True, max_digits=14, decimal_places=5)
    acctspayable = models.DecimalField(null=True, max_digits=14, decimal_places=5)

    #future additions
    #paid or unpaid (boolean)
    #related lines (many-to-many)
    

    def __unicode__(self):
        return "A ledger entry from "+str(self.date)+""

    class Meta:
        ordering = ['-id']
