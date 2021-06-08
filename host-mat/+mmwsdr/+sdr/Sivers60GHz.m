%
% Organization:	New York University
%               Pi-Radio
%
% Engineer: Panagiotis Skrimponis
%           Aditya Dhananjay
%
% Description: This class creates a fully-digital SDR with 8-channels. This
% class establish a communication link between the host and the Pi-Radio
% TCP server running on the ARM. The server configures the RF front-end and
% the ADC flow control.
%
% Last update on May 28, 2021
%
% Copyright @ 2021
%
classdef Sivers60GHz < matlab.System
    properties
        ip;				% IP address
        socket;			% TCP socket to control the Pi-Radio platform
        fpga;			% FPGA object
        isDebug;		% if 'true' print debug messages
        fc = 60e9;      % carrier frequency of the SDR in Hz
    end
    
    properties (Dependent)
        nch;    % num of channels
        ndac;   % num of D/A converters
        nadc;   % num of A/D converters
        fs;     % post-decimation/pre-interpolation sample frequency
    end
    
    methods
        function obj = Sivers60GHz(varargin)
            % Constructor
            
            % Set parameters from constructor arguments.
            if nargin >= 1
                obj.set(varargin{:});
            end
            
            % Establish connection with the Pi-Radio TCP Server.
            obj.connect();
            
            % Create the RFSoC object
            obj.fpga = mmwsdr.fpga.RFSoC('ip', obj.ip, 'isDebug', obj.isDebug);
        end
        
        function delete(obj)
            % Destructor.
            clear obj.fpga;
            
            % Close TCP connection.
            obj.disconnect();
        end
        
        function data = recv(obj, nread, nskip, nbatch)
            % Calculate the total number of samples to read:
            % (# of batch) * (samples per batch) * (# of channel) * (I/Q)
            nsamp = nbatch * nread * obj.nch * 2;
            
            write(obj.socket, sprintf("+ %d %d %d", nread/obj.fpga.npar, ...
                nskip/obj.fpga.npar, nsamp*2));
            
            % Read data from the FPGA
            data = obj.fpga.recv(nsamp);
            
            % Process the data (i.e., calibration, flow control)
            data = reshape(data, nread, nbatch, obj.nch);
            
            % Remove DC Offsets
            data = data - mean(data, 1);
        end
        
        function send(obj, data)
            % This function sends data to the FPGA and the D/A converters
            obj.fpga.send(data);
        end
        
        % Create some helper functions
        function nch = get.nch(obj)
            % Return the number of channels supported by the FPGA
            nch = obj.fpga.nch;
        end
        
        function nadc = get.nadc(obj)
            % Return the number of A/D converters of the FPGA
            nadc = obj.fpga.nadc;
        end
        
        function ndac = get.ndac(obj)
            % Return the number of D/A converters of the FPGA
            ndac = obj.fpga.ndac;
        end
        
        function fs = get.fs(obj)
            % Return the sample rate of the coverters
            fs = obj.fpga.fs;
        end
    end % methods
    
    methods (Access = 'protected')
        function connect(obj)
            % Establish connection with the Backend TCP Server.
            if (isempty(obj.socket))
                obj.socket = tcpclient(obj.ip, 8083, "Timeout", 5);
            end
        end
        
        function disconnect(obj)
            % Close the Backend TCP socket
            if (~isempty(obj.socket))
                flush(obj.socket);
                write(obj.socket, 'disconnect');
                pause(0.1);
                clear obj.socket;
            end
        end
    end
end