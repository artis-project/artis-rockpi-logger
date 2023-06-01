from setuptools import setup, find_packages, Extension
import os
import sys

import Rockfruit_DHT.platform_detect as platform_detect


BINARY_COMMANDS = [
    'build_ext',
    'build_clib',
    'bdist',
    'bdist_dumb',
    'bdist_rpm',
    'bdist_wininst',
    'bdist_wheel',
    'install',
    'clean'
]


def is_binary_install():
    do_binary = [command for command in BINARY_COMMANDS if command in sys.argv]
    return len(do_binary) > 0


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Check if an explicit platform was chosen with a command line parameter.
# Kind of hacky to manipulate the argument list before calling setup, but it's
# the best simple option for adding optional config to the setup.
platform = platform_detect.RADXA
radxa_mraa = True
# Pick the right extension to compile based on the platform.
extensions = []
if not is_binary_install():
    print('Skipped loading platform-specific extensions for Adafruit_DHT (we are generating a cross-platform source distribution).')
elif platform == platform_detect.RASPBERRY_PI:
    # Get the Pi version (1 or 2)
    if pi_version is None:
        pi_version = platform_detect.pi_version()
    # Build the right extension depending on the Pi version.
    if pi_version == 1:
        extensions.append(Extension("Rockfruit_DHT.Raspberry_Pi_Driver",
                                    ["source/_Raspberry_Pi_Driver.c", "source/common_dht_read.c", "source/Raspberry_Pi/pi_dht_read.c", "source/Raspberry_Pi/pi_mmio.c"],
                                    libraries=['rt'],
                                    extra_compile_args=['-std=gnu99']))
    elif pi_version == 2:
        extensions.append(Extension("Rockfruit_DHT.Raspberry_Pi_2_Driver",
                                    ["source/_Raspberry_Pi_2_Driver.c", "source/common_dht_read.c", "source/Raspberry_Pi_2/pi_2_dht_read.c", "source/Raspberry_Pi_2/pi_2_mmio.c"],
                                    libraries=['rt'],
                                    extra_compile_args=['-std=gnu99']))
    elif pi_version == 3:
        extensions.append(Extension("Rockfruit_DHT.Raspberry_Pi_2_Driver",
                                    ["source/_Raspberry_Pi_2_Driver.c", "source/common_dht_read.c", "source/Raspberry_Pi_2/pi_2_dht_read.c", "source/Raspberry_Pi_2/pi_2_mmio.c"],
                                    libraries=['rt'],
                                    extra_compile_args=['-std=gnu99']))
    else:
        raise RuntimeError('Detected Pi version that has no appropriate driver available.')
elif platform == platform_detect.BEAGLEBONE_BLACK:
    extensions.append(Extension("Rockfruit_DHT.Beaglebone_Black_Driver",
                                ["source/_Beaglebone_Black_Driver.c", "source/common_dht_read.c", "source/Beaglebone_Black/bbb_dht_read.c", "source/Beaglebone_Black/bbb_mmio.c"],
                                libraries=['rt'],
                                extra_compile_args=['-std=gnu99']))
elif platform == platform_detect.RADXA:
    if radxa_mraa:
        extensions.append(Extension("Rockfruit_DHT.Radxa_Zero_mraa_Driver",
                                    sources=["source/_Radxa_Zero_mraa_Driver.c", "source/common_dht_read.c", "source/Radxa_Zero/rzero_dht_mraa_read.c"],
                                    libraries=['mraa'],
                                    include_dirs=['/usr/local/include'],
                                    library_dirs=['/usr/local/lib'],
                                    extra_compile_args=['-std=gnu99'],
                                    extra_link_args=['-lmraa', '-Wall']))
    else:
        print('Using libgpiod')
        extensions.append(Extension("Rockfruit_DHT.Radxa_Zero_gpiod_Driver",
                                    sources=["source/_Radxa_Zero_gpiod_Driver.c", "source/common_dht_read.c",
                                             "source/Radxa_Zero/rzero_dht_gpiod_read.c"],
                                    libraries=['rt'],
                                    extra_compile_args=['-std=gnu99'],
                                    extra_link_args=['-lgpiod', '-Wall']))

elif platform == 'TEST':
    extensions.append(Extension("Rockfruit_DHT.Test_Driver",
                                ["source/_Test_Driver.c", "source/Test/test_dht_read.c"],
                                extra_compile_args=['-std=gnu99']))
else:
    print('Could not detect if running on the Raspberry Pi or Beaglebone Black.  If this failure is unexpected, you can run again with --force-pi or --force-bbb parameter to force using the Raspberry Pi or Beaglebone Black respectively.')
    sys.exit(1)

classifiers = ['Development Status :: 4 - Beta',
               'Operating System :: POSIX :: Linux',
               'License :: OSI Approved :: MIT License',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3',
               'Topic :: Software Development',
               'Topic :: System :: Hardware']

# Call setuptools setup function to install package.
setup(name              = 'Rockfruit_DHT',
      version           = '1.4.0',
      author            = 'Tony DiCola & Tim Parbs',
      author_email      = 'tdicola@adafruit.com, tim.parbs@gmail.com',
      description       = 'Library to get readings from the DHT11, DHT22, and AM2302 humidity and temperature sensors on a Raspberry Pi or Beaglebone Black or Radxa Zero.',
      long_description  = read('README.md'),
      license           = 'MIT',
      classifiers       = classifiers,
      url               = 'https://github.com/adafruit/Adafruit_Python_DHT/',
      packages          = find_packages(),
      ext_modules       = extensions)
