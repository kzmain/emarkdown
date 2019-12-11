
* Bottleneck of this network:
 - For fibred network on Linode LLC's clould there's no bottleneck on transmition method of this network, because all nodes are linked by fiber. The only limitation is the speed of light. 
 - For the part out of Linode company, the RTT becomes high  from Hop5, this is because of two reasons. One is light transfer time from Germany to America. Another is processing latency and queuing latency from Google's server. 
* Travers device and ISPs:
  Host -> Linode Internal Nodes (Hop 1 - Hop 3) -> DE-CIX Management GmbH (Hop 4) -> Google LLC Internal Nodes (Hop 5 - Hop 10)
* Most latency:
  In this circumstance, it is very interesting, the Linode's server is directly linked to Tier 1 ISP, DE-CIX Management GmbH. Futhermore, all nodes are connected with fiber. The most latency is introduced queuing delay and processing at Hop 4. In contrast with VU wired, it shows that the more ability of the exchange server from ISP the less (processing) latency to end users. It also shows that the last mile problem is not only related with how the data/trasmitions is/are delivered but also related with Tier 3 ISP devices' capacity.