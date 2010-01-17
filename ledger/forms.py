from django import forms
import datetime

from copressmoney.ledger.models import *


class LineForm(forms.ModelForm):
    """Form class for the LedgerLine model."""
    description = forms.CharField(required=False, widget=forms.widgets.Textarea(attrs={'rows':4, 'cols':50}))
    client = forms.ModelChoiceField(queryset=Client.objects.all().order_by('-id'), required=False)

    class Meta:
        model = LedgerLine

class SaleForm(forms.Form):
    """Form class for the form to record a new sale."""
    date = forms.DateField(initial=datetime.date.today())
    client = forms.ModelChoiceField(queryset = Client.objects.all().order_by('-id'))
    title = forms.CharField(max_length=128)
    invoice_description = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':4, 'cols':50}))
    invoice_category = forms.CharField(max_length=64)
    documentation = forms.URLField()
    upfront_price = forms.DecimalField(required=False, decimal_places=2)
    
    hosting_start_date = forms.DateField(initial=datetime.date.today())
    num_months = forms.IntegerField(required=False)
    monthly_price = forms.DecimalField(required=False, decimal_places=2)

    def clean(self):
        cleaned_data = self.cleaned_data
        monthly_price = cleaned_data.get("monthly_price")
        num_months = cleaned_data.get("num_months")
        
        if (bool(monthly_price != '') ^ bool(num_months != '')):
            raise forms.ValidationError("Number of months and monthly price must be defined together.")
        
        return cleaned_data

    def save(self):
        """Creates ledger lines and saves them to the database. """
        data = self.cleaned_data        
        d = data['date']
        c = data['client']

        def make_recognition_line_function(invoice_date, amount, client):
            description = "Invoice date "+str(invoice_date)
            def add_revenue_recognition_line(d):
                l = LedgerLine(date=d, client=client, title=client.name+" - Revenue Recognized", description=description, category="Revenue Recognized", revenue=amount, unearned=(-1*amount))
                l.save()
                return l
            return add_revenue_recognition_line      

        invoice = LedgerLine(date=d, client=c, title=data['title'], description=data['invoice_description'], documentation=data['documentation'], category=data['invoice_category'])
        invoice.acctsreceivable = (data['upfront_price']+(data['monthly_price']*data['num_months']))
        add_rr_line = make_recognition_line_function(d, data['monthly_price'], c)
        invoice.save()
        if (data['hosting_start_date'] == d):
            invoice.revenue = data['upfront_price']+data['monthly_price']
            invoice.unearned = data['monthly_price']*(data['num_months']-1)
            recognition_lines = [add_rr_line(datetime.date(d.year, d.month+i+1, d.day)) for i in xrange(data['num_months']-1)]
        else:
            invoice.revenue = data['upfront_price']
            invoice.unearned = data['monthly_price']*data['num_months']
            recognition_lines = [add_rr_line(datetime.date(data['hosting_start_date'].year, data['hosting_start_date'].month+i+1, data['hosting_start_date'].day)) for i in xrange(data['num_months'])]
        for l in recognition_lines:
            invoice.related.add(l)
        invoice.save()
        line_ids = [l.id for l in recognition_lines]
        line_ids.insert(0, invoice.id)
        return line_ids
        
