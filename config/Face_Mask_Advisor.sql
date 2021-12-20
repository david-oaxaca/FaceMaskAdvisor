CREATE DATABASE Face_Mask_Advisor;
USE Face_Mask_Advisor;

CREATE TABLE institucion
(
	id_institucion integer auto_increment primary key,
	nombre_institucion varchar(500) not null,
	correo_admin varchar(500) not null,
	nombre_admin varchar(500) not null,
	apellido_pat_admin varchar(500) not null,
	apellido_mat_admin varchar(500) not null,
	pass_admin varchar(500) not null,
    giro_institucion varchar(500) not null
);

CREATE TABLE analisis
(
	id_analisis integer auto_increment primary key,
	fecha_analisis datetime not null,
    id_estado integer not null,
	id_institucion integer not null
);

CREATE TABLE avisos
(
	id_aviso integer auto_increment primary key,
    id_estado integer not null,
    contenido varchar(500) not null
);

CREATE TABLE estados
(
	id_estado integer auto_increment primary key,
    estado varchar(500) not null
);

create unique index admin_1 on institucion(correo_admin);
alter table analisis add foreign key (id_institucion) references institucion(id_institucion);
alter table analisis add foreign key (id_estado) references estados(id_estado);
alter table avisos add foreign key (id_estado) references estados(id_estado);
