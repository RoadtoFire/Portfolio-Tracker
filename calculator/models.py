from django.db import models

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True) # e.g. MEBL
    name = models.CharField(max_length=100) # e.g. Meezan Bank
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"

class PurificationRate(models.Model):
    """
    Stores the Meezan Shariah Board rulings.
    """
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    effective_date = models.DateField() # The start date of this ruling
    impurity_percentage = models.DecimalField(max_digits=5, decimal_places=2) # e.g. 4.50

    class Meta:
        ordering = ['-effective_date'] # Newest first

    def __str__(self):
        return f"{self.stock.symbol}: {self.impurity_percentage}% ({self.effective_date})"