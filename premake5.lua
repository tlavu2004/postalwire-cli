workspace "VyiuVu"
	architecture "x64"
	startproject "Application"

	configurations
	{
		"Debug",
		"Release",
		"Dist"
	}

outputdir = "%{cfg.buildcfg}-%{cfg.system}-%{cfg.architecture}"

include "Functions"
include "Application"
