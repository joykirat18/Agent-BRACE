.. meow-tea-taro documentation master file, created by
   sphinx-quickstart on Mon Oct 13 05:42:19 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

meow-tea-taro documentation
===========================

**Meow Tea Taro** is a Multi-turn Agentic Reinforcement Learning Framework for training agents in interactive environments like TextWorld and ALFWorld.

.. note::
   This project is under active development. APIs may change between versions.

We use `verl <https://github.com/volcengine/verl>`_ as the backbone architecture. 
We make minimum modifications to **verl** and provide a **ready-to-use** and **customizable** framework for training multi-turn agentic RL.
The learning curve for **meow-tea-taro** would be very low if you are already familiar with **verl**.

Features
--------


.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting_started/quick_install
   getting_started/quick_start_textworld

.. toctree::
   :maxdepth: 2
   :caption: Tutorials

   tutorials/basic_training
   tutorials/custom_environments
   tutorials/data_preparation

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/modules

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
