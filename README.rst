***********
Cloud Crony
***********

RESTful Scheduling as a Service: Scheduled Tasks for the Cloud

:version: 0.0.0

**Table of Contents**

.. contents::
    :local:
    :depth: 2
    :backlinks: none

========
Features
========

Here are some of the planned features for the first release::

    * Easy to deploy
        - one command to acquire libraries (pip!)
        - one command worker registration
        - one command API setup
    * Guaranteed task execution - no missed jobs
    * Secure by default - sandboxed execution for workers
    * Autoscaling - need more workers? Cloud Crony can spin them up for you
    * Python 2.7+ and 3.3+ supported
    * RESTful - client bindings can be in any language that can speak HTTP/JSON
    * Familiar scheduling syntax - welcome back, Cron.

==========
Extensions
==========

The following are a list of potential extensions to the scheduling service::

    * Tenanted service - namespace schedules by tenant
    * Scheduling profiles 
        * Maximum per task runtime
        * Maximum concurrent tasks
        * Preemption allowed
    * Task groups - in conjunction with profiles 
        * /schedules/{group}/tasks/
        * Allow special configuration for group
    * Autoscaling 
    * Preemptive scheduling 
    * Prioritized scheduling 
        * Assign task priorities
        * Choose next task based on priority + dealine
    * Real-time scheduling 
        * Fail tasks that take too long
        * Specify task deadline as well as periodicity
            * Task deadline given relative to periodicity 
    * Improved security
        * Better sandboxing
    * Error reporting task specification
        * error_hook: task to handle main process errors
        * similar to progress hook
        * Appends them to GET /schedules/{id} "errors" field
    * Client bindings
    * Backend configuration options and drivers
        * MongoDB
        * Redis
        * sqlite
        * Some sort of Cloud DB

===========
Development
===========

The core maintainer is Allele Dev
<allele.dev@gmail.com>. Feel free to reach out to him with
any questions you have.

=======
License
=======

Copyright 2016 Allele Dev

Licensed under the Apache License, Version 2.0 (the "License"); you
may not use this file except in compliance with the License.  You may
obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied.  See the License for the specific language governing
permissions and limitations under the License.
