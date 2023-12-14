# Basic Vivado and Pynq tutorials

In this lession, we will build a system with Vivado using the pre-built xilinx blocks/ips. We can aslo add our own custom ips but that is left for future lessons. In Vivado specifically we create the entire system with PS and PL blocks and their interfaces and finally generate the .bit aand .hwh files for the design, which are then used in Pynq to control these hardware entitiesfrom software.

## 1.Introduction to Vivado 
This is a good [tutorial](https://discuss.pynq.io/t/tutorial-creating-a-hardware-design-for-pynq/145) from the Pynq community that gives the basic idea of all the necessary steps in Vivado.

## 2.Useful sample project - Using the DMA
This 3 part tutorial [Part-1](https://discuss.pynq.io/t/tutorial-pynq-dma-part-1-hardware-design/3133)  [Part-2](https://discuss.pynq.io/t/tutorial-pynq-dma-part-2-using-the-dma-from-pynq/3134) is an extension of the previous tutorial. The design followed here allows us to write some data through pynq into the PS-DRAM and then send the data to the PL using the DMA interface. The PL has a FIFO queue which takes in the input and sends back the same data (with some delay). The received data is then stored again in the PS-DRAM, in a different allocation. Vivado defines the path for the data that is generated and scheduled using Pynq/python. 

The tutorial explains what a DMA is and how it works. We've added some changes in the end.

**Note**:In case of different Vivado versions the location of the .bit amf .hwh files may sometimes differ. They may also have different names. Make sure to rename them properly as shown in the images below, where we have renamed the .bit and .hwh files to dma_test.xxx.

<p align="center">
<img src="pic2.png" alt="Alt Text" width="700" height="400">
</p>

<p align="center">
<img src="pic1.png" alt="Alt Text" width="500" height="500">
</p>

Then upload them into the RFSoC Sd-card theough the Pynq notebook and rename them if necessary.

After that we can start to import the ghardwrae design as an Overlay and start writing python commands to define the behaviour of the entire system.
