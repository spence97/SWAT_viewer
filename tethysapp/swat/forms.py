from django.forms import ModelForm
from .model import new_watershed


class UploadWatershedForm(ModelForm):
    class Meta:
        model = new_watershed
        fields = ('watershed_name', 'streams_shapefile', 'basins_shapefile', 'monthly_rch_file', 'daily_rch_file')

