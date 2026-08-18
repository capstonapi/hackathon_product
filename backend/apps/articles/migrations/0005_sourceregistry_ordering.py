from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("articles", "0004_enforced_governance")]

    operations = [
        migrations.AlterModelOptions(
            name="sourceregistry",
            options={"ordering": ["priority", "source"]},
        ),
    ]
