---
layout: page
title: agent_design
description: From Universal Humanoid Control to Automatic Physically Valid Character Creation
img: /assets/img/projects/agent_design/agent_design.gif
importance: 3
type: research
---

<h3 style="text-align: center;font-size:30px"> From Universal Humanoid Control to Automatic Physically Valid Character Creation </h3>
<h4 style="text-align: center;color:DodgerBlue"> Zhengyi Luo, Ye Yuan, Kris M. Kitani  </h4>
<h5 style="text-align: center;"> In Submission </h5>

<div class="row">
    <div class="col-sm-12 mt-3 mt-md-0 mx-md-0 ml-md-0">
        <img class="img-fluid rounded z-depth-0" src="{{ '/assets/img/projects/agent_design/humangoid_design.jpg' | relative_url }}" alt="" title="Kin-Poly image"/>
    </div>
</div>

<!-- <div class="caption">
    This image can also have a caption. It's like magic.
</div> -->
<br>
<p  align="justify">
    Automatically designing virtual humans and humanoids holds great potential in aiding the character creation process in games, movies, and robots. In some cases, a character creator may wish to design a humanoid body customized for certain motions such as karate kicks and parkour jumps. In this work, we propose a humanoid design framework to automatically generate physically valid humanoid bodies conditioned on sequence(s) of pre-specified human motions. First, we learn a generalized humanoid controller trained on a large-scale human motion dataset that features diverse human motion and body shapes. Second, we use a design-and-control framework to optimize a humanoid's physical attributes to find body designs that can better imitate the pre-specified human motion sequence(s). Leveraging the pre-trained humanoid controller and physics simulation as guidance, our method is able to discover new humanoid designs that are customized to perform pre-specified human motions.
</p>

<h3 style="color:darkblue">Demo Video</h3>
<div class="embed-container">
<center>
  <iframe
      src="https://www.youtube.com/embed/uC0P2iB56kM"
      width="700"
      height="480"
      frameborder="0"
      allowfullscreen="">
  </iframe>
  </center>
</div>

<!-- <br>
<br>
<br>
<h3 style="color:darkblue">Paper and Code</h3>

<div>
{% for paper in site.data.publications.publications %}
    {% if paper.title ==  "From Universal Humanoid Control to Automatic Physically Valid Character Creation" %}
        {% include single_paper.html %}
    {% endif %}
{% endfor %}
</div> -->

<br>
<br>
<br>
<p> -- </p>
