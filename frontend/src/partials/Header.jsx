/* eslint-disable react/prop-types */

import { IoCalendarClearSharp } from 'react-icons/io5'

const Header = ({ title = 'Dashboard', children }) => {
	const currentDate = new Date().toLocaleDateString('en-US', {
		month: 'long',
		day: 'numeric',
		year: 'numeric',
	})
	const currentTime = new Date().toLocaleTimeString([], {
		hour: 'numeric',
		minute: '2-digit',
	})
	return (
		<div className='sticky top-0 z-10 bg-darkblue pt-10 pb-4'>
			<div className='flex flex-row justify-between items-center lg:ml-0 mt-3 text-white'>
				<div className=' flex flex-col   md:flex-row gap-x-4 ml-10 lg:ml-0 lg:gap-x-10 items-center'>
					<div className='font-semibold tracking-wider text-gray-300 text-xl'>
						{title.toUpperCase()}
					</div>
					{children}
				</div>
				<div className=' flex-row justify-end hidden lg:flex'>
					<div className='p-2 px-4 rounded-md lg:rounded-3xl gap-6 font-semibold flex flex-row items-center justify-between bg-[#1A2833]'>
						<IoCalendarClearSharp className='text-[20px] text-gray-300'></IoCalendarClearSharp>
						<div className='font-medium text-xs text-gray-300'>
							{currentDate} | {currentTime}
						</div>
					</div>
				</div>
			</div>
		</div>
	)
}

export default Header
