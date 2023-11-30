# Picky

Picky is an open-source web application firewall project.

Traffic will pass as follows:
                       +-------------+
   +------+            |    Web      |            +------------+
   | Host |  => => =>  | Application |  => => =>  | Web server |
   +------+            |  Firewall   |            +------------+
                       +-------------+
