---
layout: page
title: MEVA
description: "3D Human Motion Estimation via Motion Compression and Refinement"
img: /assets/img/projects/meva.gif
importance: 4
type: research
---

<h3 style="text-align: center;font-size:30px"> 3D Human Motion Estimation via Motion Compression and Refinement </h3>
<h4 style="text-align: center;color:DodgerBlue"> Zhengyi Luo, S. Alireza Golestaneh, Kris M. Kitani  </h4>
<h5 style="text-align: center;"> ACCV 2020, Oral Presentation </h5>


<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        <img class="img-fluid rounded z-depth-1" src="{{ '/assets/img/projects/meva_teaser.png' | relative_url }}" alt="" title="example image"/>
    </div>
</div>
<!-- <div class="caption">
    This image can also have a caption. It's like magic.
</div> -->
<br>
<p  align="justify">
    We develop a technique for generating smooth and accurate 3D human pose and motion estimates from RGB video sequences. Our technique, which we call Motion Estimation via Variational Autoencoder (MEVA), decomposes a temporal sequence of human motion into a smooth motion representation using auto-encoder-based motion compression and a residual representation learned through motion refinement. This two-step encoding of human motion captures human motion in two stages: a general human motions estimation step that captures the coarse overall motion, and a residual estimation that adds back person-specific motion details. Experiments show that our method produces both smooth and accurate 3D human pose and motion estimates.

</p>

<br>

<h3 style="color:darkblue">Talk</h3>

<div class="embed-container">
<center>
  <iframe
      src="https://www.youtube.com/embed/-TN3NRpCEc0"
      width="700"
      height="480"
      frameborder="0"
      allowfullscreen="">
  </iframe>
  </center>
</div>


<h3 style="color:darkblue">Demo</h3>

<div class="embed-container">
<center>
  <iframe
      src="https://www.youtube.com/embed/YBb9NDz3ngM"
      width="700"
      height="480"
      frameborder="0"
      allowfullscreen="">
  </iframe>
  </center>
</div>







<br>
<br>
<br>
<h3 style="color:darkblue">Paper and Code</h3>

<div>
{% for paper in site.data.publications.publications %}
    {% if paper.title ==  "3D Human Motion Estimation via Motion Compression and Refinement" %}
        {% include single_paper.html %}
    {% endif %}
{% endfor %}
</div>

<br>
<br>
<br>
<p> -- </p>