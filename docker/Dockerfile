FROM archlinux/base

WORKDIR /home

COPY . .

RUN pacman -Sy
RUN pacman -S --noconfirm --needed - < arch_dependencies.txt
RUN pip install --trusted-host pypi.python.org -r python_dependencies.txt
