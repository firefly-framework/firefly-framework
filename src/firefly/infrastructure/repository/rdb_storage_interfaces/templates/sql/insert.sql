insert into {% block fqtn %}{{ fqtn | sqlsafe }} {% endblock %} (

{%- block columns -%}
    {%- for column in data[0].keys() -%}
        {{ _q | sqlsafe }}{{ column | sqlsafe }}{{ _q | sqlsafe }}{% if not loop.last %},{% endif %}
    {%- endfor -%}
{% endblock %}

) values

{%- block values -%}
    {% for item in data %}
        (
        {%-  for column, value in item.items() -%}
            {% block insert_value scoped %}{{ value }}{% endblock %}
            {% if not loop.last %},{% endif %}
        {%- endfor -%}
        )
        {% if not loop.last %},{% endif %}
    {% endfor %}
{%- endblock -%}

{%- block after -%}{%- endblock -%}
