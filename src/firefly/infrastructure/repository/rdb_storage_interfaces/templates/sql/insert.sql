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
        {%-  for value in item.values() -%}
            {{ value }}{% if not loop.last %},{% endif %}
        {%- endfor -%}
        )
        {% if not loop.last %},{% endif %}
    {% endfor %}
{%- endblock -%}

{%- block after -%}{%- endblock -%}
