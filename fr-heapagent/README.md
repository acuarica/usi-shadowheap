Low Level Native Java Instrumentation Framework
===============================================

# Introduction

Why instrument?
*  Better control
*  Aspect programming
*  and?


# Related work

Ability to **instrument** the JVM by only adding a small agent.


Usually to instrument the *JVM* another JVM is needed.
To instrument regular applications this is just fine,
but when you need to instrument the java library itself you encounter bootstrap problems.
That is why a native approach is more accurate.

Instrumentation and client code are more coupled, this is how it should be.

It allows to simplify the development because you do not need a TCP 
connection to instrument code on other JVM process.
Lowoverhead agent.
Modular parser, you pay what you need. Full power of templates for better performance.

# Development

Modular parser using templates.

# Evaluation

# Conclusions

# References

TODO:
Implement the agent in several JVMs, at least Oracle, Jikes and IBM.

> ## To be published in PPPJ'14.
> Why PPPJ is the best fit for this article?
> They allow tool papers, and that is exacty what it is.


TODO: try to come up with an performance evaluation (maybe against asm, disl, bcel) also with gui apps 
like eclipse, netbeans.
 
try diffents kind of instrumentations.
