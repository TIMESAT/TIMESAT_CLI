Quick Start HRVPP:
1. Set up your Python environment: Install the environment defined in TIMESAT_python.yml.
2. Compile the Fortran routines: Execute compile_TIMESAT_linux_macOS.sh.
3. Run the application: 
    python main.py settings_test.json







Quick Start HRVPP:
1. Set up your Python environment: Install the environment defined in TIMESAT_python.yml.
2. Generate input file lists: Run create_file_list.py.
3. Compile the Fortran routines: Execute compile_TIMESAT_linux_macOS.sh.
4. Run the application: Launch main.py using settings.json for configuration.

Additional inforamtion of HRVPP QFLAG2:
                        w = ones(size(vi));
                        w(Q2==1) = 1;
                        w(Q2==4097) = 1;
                        w(Q2==8193) = 1;
                        w(Q2==12289) = 1;
                        w(Q2==1025) = 0.5;
                        w(Q2==9217) = 0.5;
                        w(Q2==2049) = 0.5;
                        w(Q2==6145) = 0.5;
                        w(Q2==3073) = 0.5;
