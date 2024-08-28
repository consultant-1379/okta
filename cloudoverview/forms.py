from .models import PotentialCloud
from bootstrap_modal_forms.forms import BSModalModelForm

class PotentialCloudModelForm(BSModalModelForm):
    class Meta:
        model = PotentialCloud
        fields = ['cloud_name', 'version', 'cpu_contention', 'total_cpu', 'ram_contention', 'total_ram', 'storage', 'number_of_hosts', 'provisioning',]