from rest_framework import serializers
from TransApp.models import Transaction
from datetime import timedelta

class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Transaction model
    """
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['id', 'stock', 'transaction_type', 'price', 'quantity', 'timestamp']
    
    def get_timestamp(self, obj):
        """
        Returns the timestamp of the transaction in the format '%Y-%m-%d %H:%M'
        """
        adjusted_timestamp = obj.timestamp + timedelta(hours=8)
        return adjusted_timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    def create(self, validated_data):
        """
        Creates a new transaction with the validated data and the user from the request context
        """
        user = self.context['request'].user
        transaction = Transaction.objects.create(user=user, **validated_data)
        return transaction
    


