create {% block object_type %}schema{% endblock %} {% block create_condition %}if not exists{% endblock %} {% block context_name %}{{ context_name | sqlsafe }}{% endblock %}
