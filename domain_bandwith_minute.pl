#!/usr/bin/perl -w
use strict;
use POSIX qw(strftime);
use Carp;



sub getLogFile
{
	my $dir = shift; 
	opendir DIR, $dir or confess "open $dir error";
	my @file = grep { $_ =~ /\.access\.log$/ } readdir( DIR ); 
	return wantarray ? @file : \@file;
}


sub getFileLength
{
	my ( $path, $file  ) = @_;
	my %data;
	my $current = strftime( "%d/%b/%Y:%H:%M", localtime(time() - 60) );
	my $realFile = $path . '/' . $file;
	my @content = grep { $_ =~ /$current/ } `tail -50001 $realFile`;
	my $line = shift @content;
	my $domain = $file =~ s/(.*?)_.*\.access.log/$1/ 
					? $file . '.wandoujia.com' 
					: $file =~ s/(.*?).access.log/$1\.wandoujia\.com/
					? $file : 'UNKNOWN';

	
	foreach ( @content ){
		my @line = split /\s+/;
		$data{$domain} = 0 if not defined $data{$domain};
		$data{$domain} += $line[9] if $line[9] =~ /\d+/;
	}
	return wantarray ? %data : \%data;
}


sub main
{

	my %total;
	my %tmp;
	my $path = "/home/work/nginx/logs";
	my @file = getLogFile( "/home/work/nginx/logs" );
	for my $file ( @file ){
		%tmp = getFileLength( $path, $file );	 	
		map{
			$total{$_} = 0 if not defined $total{$_};
			$total{$_} += $tmp{$_};	
		} keys %tmp;
	}
	for ( keys %total ){
		printf "%s=%.2f\n", $_, $total{$_}/60 ;
	}
}

main()
