High-Precision π Calculator
========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   readme
   api
   benchmarks

Introduction
------------

This package provides a high-precision implementation of π calculation using the Chudnovsky algorithm.
The implementation is designed for accuracy, performance, and ease of use.

Quick Start
----------

Installation
^^^^^^^^^^^

.. code-block:: bash

   pip install compute-pi

Basic Usage
^^^^^^^^^^

.. code-block:: python

   from compute_pi import PiCalculator

   # Initialize calculator
   calculator = PiCalculator(precision=1000)

   # Compute π
   result = calculator.compute_pi()
   print(calculator.format_result(result))

API Documentation
---------------

.. toctree::
   :maxdepth: 2

   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 