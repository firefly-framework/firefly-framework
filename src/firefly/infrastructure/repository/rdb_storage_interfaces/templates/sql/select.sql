select

{% for column in columns %}
    {{ _q | sqlsafe }}{{ column | sqlsafe }}{{ _q | sqlsafe }}{% if not loop.last %},{% endif %}
{% endfor %}

from {% block fqtn %}{{ fqtn | sqlsafe }}{% endblock %}

{% if criteria %}
    where
    {% import "sql/macros.sql" as macros %}
    {% block where_clause scoped %}{{ macros.where_clause(criteria) }}{% endblock %}
{% endif %}

{% if limit %}
    limit {{ limit | sqlsafe }}
{% endif %}

{% if offset %}
    offset {{ offset | sqlsafe }}
{% endif %}
