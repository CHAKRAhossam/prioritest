\NeedsTeXFormat{LaTeX2e}

\ProvidesClass{rapport}[2025/11/12 Classe rapport]

% Base
\LoadClass[a4paper,12pt]{article}

% --------------------- Packages ------------------------

\RequirePackage[french]{babel}
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage{lmodern}
\RequirePackage{mathtools}
\RequirePackage{siunitx}
\RequirePackage{graphicx}
\RequirePackage{float} % pour l'option [H]
\RequirePackage[justification=centering]{caption}
\captionsetup[figure]{position=bottom} % légende sous l'image
\RequirePackage{subcaption}
\RequirePackage{wallpaper}
\RequirePackage{nomencl}
\RequirePackage{fancyhdr}
\RequirePackage{url}
\RequirePackage[hidelinks]{hyperref}
\RequirePackage[left=2.5cm,right=2.5cm,top=2cm,bottom=3.5cm]{geometry}
\RequirePackage[section]{placeins} % barrières de flottants par section
\RequirePackage{etoolbox}

% Barrières de flottants avant chaque titre :
\preto\section{\FloatBarrier}
\preto\subsection{\FloatBarrier}
\preto\subsubsection{\FloatBarrier}

% -------------------- Informations sur le rapport ----------------------

% après \cours{...}, \cours devient le texte fourni (même logique pour les autres)
\newcommand{\cours}[1]{\renewcommand{\cours}{#1}}
\newcommand{\sujet}[1]{\renewcommand{\sujet}{#1}}
\newcommand{\titre}[1]{\renewcommand{\titre}{#1}}
\newcommand{\enseignant}[1]{\renewcommand{\enseignant}{#1}}
\newcommand{\eleves}[1]{\renewcommand{\eleves}{#1}}
\newcommand{\logo}[1]{\renewcommand{\logo}{#1}}
\newcommand{\unif}[1]{\renewcommand{\unif}{#1}}

% -------------------- En-têtes ----------------------

\newcommand{\fairemarges}{%
  \makenomenclature
  \pagestyle{fancy}
  \fancyheadoffset{1cm}
  \setlength{\headheight}{2cm}
  \lhead{\includegraphics[scale=0.15]{\logo}}%
  \rhead{\nouppercase{\leftmark}}%
}

% -------------------- Page de garde ----------------------

\newcommand{\fairepagedegarde}{%
\begin{titlepage}
  \centering
  \includegraphics[width=0.5\textwidth]{\logo}\par\vspace{1cm}
  {\scshape\LARGE \unif \par}
  \vspace{1.5cm}
  {\scshape\Large \cours \\ \sujet \\ Rapport\par}
  \vspace{1cm}
  \rule{\linewidth}{0.2 mm} \\[0.4 cm]
  {\huge\bfseries \titre \par}
  \rule{\linewidth}{0.2 mm} \\[1.5 cm]
  \vspace{1cm}
  \begin{minipage}{0.5\textwidth}
    \begin{flushleft}\large
      \emph{\textbf{Élèves :}}\\
      \eleves
    \end{flushleft}
  \end{minipage}
  \hfill
  \begin{minipage}{0.4\textwidth}
    \begin{flushright}\large
      \emph{\textbf{Enseignant :}}\\
      \enseignant
    \end{flushright}
  \end{minipage}\\[4cm]
  \vfill
  {\large \today\par}
\end{titlepage}
}

% -------------------- Table des matières ----------------------

\newcommand{\tabledematieres}{%
  \tableofcontents
  \newpage
}

% -------------------- Insertion d'images ----------------------

% Légende sous l'image, placement strict [H], label sans espace.
% Usage : \insererfigure{chemin}{8cm}{Ma légende}{mon-label}
\newcommand{\insererfigure}[4]{%
  \begin{figure}[H]
    \centering
    \includegraphics[width=#2,keepaspectratio]{#1}% image d'abord
    \caption{#3}% légende ensuite => s'affiche en bas
    \label{fig:#4}% label après \caption pour une numérotation correcte
  \end{figure}
}

% Variante avec placement optionnel :
% \insererfigureopt[ht]{chemin}{8cm}{Ma légende}{mon-label}
\newcommand{\insererfigureopt}[5][H]{%
  \begin{figure}[#1]
    \centering
    \includegraphics[width=#2,keepaspectratio]{#3}
    \caption{#4}
    \label{fig:#5}
  \end{figure}
}

