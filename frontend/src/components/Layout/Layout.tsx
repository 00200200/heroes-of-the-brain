import React from 'react';

interface Props {
	children: React.ReactNode;
}

export default function Layout({ children }: Props) {
	return (
		<div className='min-h-screen'>
			<main className='max-w-7xl mx-auto px-5 py-10'>{children}</main>
		</div>
	);
}
