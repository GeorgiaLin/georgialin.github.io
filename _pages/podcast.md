---
layout: page
title: podcast
permalink: /podcast/
nav: true
---
{% include podcast_styles.html %}

<div class="pod-hero">
  <img src="{{ site.data.podcast_channel.cover | relative_url }}" alt="{{ site.data.podcast_channel.title }}" />
  <div class="pod-meta">
    <h1>{{ site.data.podcast_channel.title }}</h1>
    <div class="pod-tagline">{{ site.data.podcast_channel.description }}</div>
    <div class="pod-subscribe">
      {% if site.data.podcast_channel.apple %}<a class="pod-btn" href="{{ site.data.podcast_channel.apple }}" target="_blank">🎧 Apple Podcasts</a>{% endif %}
      {% if site.data.podcast_channel.spotify %}<a class="pod-btn" href="{{ site.data.podcast_channel.spotify }}" target="_blank">🟢 Spotify</a>{% endif %}
      {% if site.data.podcast_channel.xiaoyuzhou %}<a class="pod-btn" href="{{ site.data.podcast_channel.xiaoyuzhou }}" target="_blank">🎙️ 小宇宙</a>{% endif %}
      {% if site.data.podcast_channel.rss %}<a class="pod-btn rss" href="{{ site.data.podcast_channel.rss }}" target="_blank">🔗 RSS</a>{% endif %}
    </div>
  </div>
</div>

<p style="color:#666; margin-top:18px; font-size:15px;">
  你可以直接在这里收听，也可以在 Apple Podcasts、Spotify、小宇宙 上订阅。点开每一集查看时间轴与文字稿。
</p>

<ul class="pod-list">
  {% assign episodes = site.podcast | sort: "number" | reverse %}
  {% for ep in episodes %}
  <li class="pod-ep">
    <div class="pod-ep-top">
      <h3><a href="{{ ep.url | relative_url }}">{{ ep.title }}</a></h3>
      <span class="pod-ep-date">{{ ep.date | date: "%Y-%m-%d" }}{% if ep.duration %} · {{ ep.duration }}{% endif %}</span>
    </div>
    {% if ep.summary %}<div class="pod-ep-sum">{{ ep.summary | truncate: 110 }}</div>{% endif %}
    <audio controls preload="none">
      <source src="{{ ep.audio }}" />
    </audio>
    <div style="margin-top:8px;">
      <a class="pod-ep-link" href="{{ ep.url | relative_url }}">时间轴 / 文字稿 →</a>
    </div>
  </li>
  {% endfor %}
</ul>
