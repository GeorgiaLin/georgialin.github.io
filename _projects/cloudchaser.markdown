---
layout: page
title: Cloud Chaser
description: "Cloud Chaser: Real Time Deep Learning Computer Vision on Low Computing Power Devices"
img: /assets/img/projects/chase.jpg
importance: 5
type: research
---

<h3 style="text-align: center;font-size:30px"> Cloud Chaser: Real Time Deep Learning Computer Vision on Low Computing Power Devices </h3>
<h4 style="text-align: center;color:DodgerBlue"> Zhengyi Luo, Austin Small, Liam Dugan, Stephen Lane  </h4>
<h5 style="text-align: center;"> ICMV 2018 </h5>


<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        <img class="img-fluid rounded z-depth-1" src="{{ '/assets/img/projects/cloud_chaser_arch.png' | relative_url }}" alt="" title="example image"/>
    </div>
</div>
<!-- <div class="caption">
    This image can also have a caption. It's like magic.
</div> -->
<br>
<p  align="justify">
    Internet of Things(IoT) devices, mobile phones, and robotic systems are often denied the power of deep learning algorithms due to their limited computing power. However, to provide time-critical services such as emergency response, home assistance, surveillance, etc, these devices often need real-time analysis of their camera data. This paper strives to offer a viable approach to integrate high-performance deep learning-based computer vision algorithms with low-resource and low-power devices by leveraging the computing power of the cloud. By offloading the computation work to the cloud, no dedicated hardware is needed to enable deep neural networks on existing low computing power devices. A Raspberry Pi based robot, Cloud Chaser, is built to demonstrate the power of using cloud computing to perform real-time vision tasks. Furthermore, to reduce latency and improve real-time performance, compression algorithms are proposed and evaluated for streaming real-time video frames to the cloud.

</p>

<br>


<h3 style="color:darkblue">Demo</h3>

<div class="embed-container">
<center>
  <iframe
      src="https://www.youtube.com/embed/8ALi8_fJVNU"
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
    {% if paper.title ==  "Cloud Chaser: Real Time Deep Learning Computer Vision on Low Computing Power Devices" %}
        {% include single_paper.html %}
    {% endif %}
{% endfor %}
</div>

<br>
<br>
<br>
<p> -- </p>