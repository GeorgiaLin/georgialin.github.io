---
layout: page
title: podcast
permalink: /podcast/
nav: true
---
{% include podcast_styles.html %}

<div class="pod-hero">
  <img class="pod-cover" src="{{ site.data.podcast_channel.cover | relative_url }}" alt="{{ site.data.podcast_channel.title }}" />
  <div class="pod-meta">
    <h1>{{ site.data.podcast_channel.title }}</h1>
    <div class="pod-tagline">{{ site.data.podcast_channel.description }}</div>
    {% include podcast_subscribe.html %}
  </div>
</div>

<ul class="pod-list">
  {% assign episodes = site.podcast | sort: "number" | reverse %}
  {% for ep in episodes %}
  <li class="pod-ep">
    <a class="pod-ep-link" href="{{ ep.url | relative_url }}">
      <div class="pod-ep-top">
        <h3>{{ ep.title }}</h3>
        <span class="pod-ep-date">{{ ep.date | date: "%Y-%m-%d" }}{% if ep.duration %} · {{ ep.duration }}{% endif %}</span>
      </div>
      {% if ep.summary %}<div class="pod-ep-sum">{{ ep.summary | truncate: 96 }}</div>{% endif %}
    </a>
  </li>
  {% endfor %}
</ul>
