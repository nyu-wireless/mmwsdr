%% DEMO: Basic Tx/Rx with the Sivers 60 GHz, 1 channel SDR

%% Packages
% Add the folder containing +mmwsdr to the MATLAB path.
addpath('../../');

%% Parameters
%
%                              | Control    | Data 1     | Data 2     |
% sdr2-in1.sb1.cosmos-lab.org: | 10.113.6.3 | 10.114.6.3 | 10.115.6.3 |
% sdr2-in2.sb1.cosmos-lab.org: | 10.113.6.4 | 10.114.6.4 | 10.115.6.4 |
%
ip = "10.1.1.43";	% IP Address
isDebug = true;		% print debug messages

%% Create a SDR
sdr0 = mmwsdr.sdr.Sivers60GHz('ip', ip, 'isDebug', isDebug);

% Configure the RFSoC
sdr0.fpga.configure('../../config/rfsoc.cfg');

%% Send data
nFFT = 1024;            % number of FFT points
txPower = 10000*1;      % transmit
scMin = -250;
scMax = 250;
constellation = [1+1j 1-1j -1+1j -1-1j];

txfd = zeros(nFFT, sdr0.nch);
txfd(nFFT/2 + 1 + (scMin:scMax),:) = ...
    constellation(randi(4,length(scMin:scMax),sdr0.nch));
txfd = fftshift(txfd);
txtd = ifft(txfd);

% Normalize the energy of the tx array and scale with txPower.
txtd = txPower*txtd./max(abs(txtd));

sdr0.send(txtd);

%% Receive data

% To read data from the ADCs we use the `recv` method of the FullyDigital
% sdr class. This method has 3 arguments.
% * nsamp: number of continuous samples to read
% * nskip: number of samples to skip
% * nbatch: number of batches

nFFT = 1024;	% num of FFT points
nskip = 1024*3;	% skip ADC data for 1024 cc
nbatch = 200;	% num of batches

rxtd = sdr0.recv(nFFT, nskip, nbatch);

%% Plot the received data
scs = linspace(-nFFT/2, nFFT/2-1, nFFT);
for ibatch=1:10
    % Plot the frequency-domain signal
    f = figure(2);
    plot(scs, mag2db(abs(fftshift(fft(rxtd(:,ibatch))))));
    axis tight; grid on; grid minor;
    ylabel('Magnitude [dB]', 'interpreter', 'latex', 'fontsize', 12);
    xlabel('Subcarrier Index', 'interpreter', 'latex', 'fontsize', 12);
end

%% Close the TCP connection to the SDR
clear sdr0