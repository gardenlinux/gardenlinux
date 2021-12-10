ARG build_base_image=gardenlinux/build
FROM	$build_base_image

RUN	sudo apt-get update \
     &&	sudo apt-get install -y \
		libelf1 git vim build-essential dh-make devscripts dkms

# Install Garden Linux Kernel Build Dependencies for out of tree modules
COPY packages/ /packages
RUN sudo dpkg -i /packages/linux-kbuild*.deb
RUN sudo dpkg -i /packages/linux-compiler-gcc*.deb
RUN sudo dpkg -i /packages/linux-headers*.deb
