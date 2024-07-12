/* eslint-disable react/prop-types */

import { useState } from 'react'
import sampleTableData from '../data/sampleTableData'

const CustomTable = () => {
	const [currentPage, setCurrentPage] = useState(1)
	const itemsPerPage = 6
	const totalPages = Math.ceil(sampleTableData.length / itemsPerPage)

	const handlePageChange = (page) => {
		setCurrentPage(page)
	}

	const startIndex = (currentPage - 1) * itemsPerPage
	const endIndex = startIndex + itemsPerPage
	const currentData = sampleTableData.slice(startIndex, endIndex)

	return (
		<div className='relative overflow-x-auto shadow-md sm:rounded-md'>
			<table className='w-full text-sm text-left rtl:text-right text-white  border border-darkblueLight rounded-md'>
				<thead className='text-xs uppercase text-white bg-darkblueLight   '>
					<tr className=''>
						{/* <th scope='col' className='p-4'>
							<div className='flex items-center'>
								<label for='checkbox-all-search' className='sr-only'>
									checkbox
								</label>
							</div>
						</th> */}
						<th scope='col' className='px-6 py-3'>
							Function name
						</th>
						<th scope='col' className='px-6 py-3'>
							Runtime
						</th>
						<th scope='col' className='px-6 py-3'>
							All duration(s)
						</th>
						<th scope='col' className='px-6 py-3'>
							Provisioned memory
						</th>
						<th scope='col' className='px-6 py-3'>
							Memory cost
						</th>
						<th scope='col' className='px-6 py-3'>
							Invocation cost
						</th>
						<th scope='col' className='px-6 py-3'>
							Total cost
						</th>
						<th scope='col' className='px-6 py-3'>
							Avg cost/invocation
						</th>
					</tr>
				</thead>
				<tbody className=''>
					{currentData.map((data, index) => (
						<tr
							key={index}
							className={`${index % 2 === 0 ? 'bg-darkblueMedium' : 'bg-transparent'} cursor-pointer  text-xs  hover:bg-gray-50 dark:hover:bg-gray-600`}
						>
							{/* <td className='w-4 p-4'>
								<div className='flex items-center'>
									<input
										id='checkbox-table-search-1'
										type='checkbox'
										className='w-4 h-4 text-lambdaPrimary bg-gray-100 border-gray-300 rounded focus:text-lambdaPrimary dark:focus:text-lambdaPrimary dark:ring-offset-gray-800 dark:focus:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'
									/>
									<label for='checkbox-table-search-1' className='sr-only text-red-600'>
										checkbox
									</label>
								</div>
							</td> */}
							<td className='px-6 py-6  text-wrap'>{data.function_name}</td>
							<td className='px-6 py-3'>{data.runtime}</td>
							<td className='px-6 py-3'>{data.all_duration.toFixed(6)}</td>
							<td className='px-6 py-3'>{data.provisioned_memory.toFixed(6)}</td>
							<td className='px-6 py-3'>{data.memory_cost.toFixed(6)}</td>
							<td className='px-6 py-3'>{data.invocation_cost.toFixed(7)}</td>
							<td className='px-6 py-3'>{data.total_cost.toFixed(6)}</td>
							<td className='px-6 py-3'>{data.avg_cost_per_invocation.toFixed(6)}</td>
						</tr>
					))}
				</tbody>
			</table>
			<nav
				className='flex items-center flex-column flex-wrap md:flex-row justify-between pt-8'
				aria-label='Table navigation'
			>
				<span className='text-xs font-light text-gray-500 dark:text-gray-400 mb-4 md:mb-0 block w-full md:inline md:w-auto'>
					Showing{' '}
					<span className='font-light text-gray-900 dark:text-white'>
						{startIndex + 1}-{Math.min(endIndex, sampleTableData.length)}
					</span>{' '}
					of{' '}
					<span className='font-light text-gray-900 dark:text-white'>
						{sampleTableData.length}
					</span>
				</span>
				<div className='flex flex-row '>
					<div className='flex items-center mt-4 md:mt-0 text-white space-x-8 cursor-pointer'>
						<div
							className='flex flex-row  items-center text-white text-xs space-x-2'
							onClick={() => handlePageChange(currentPage - 1)}
						>
							<p
								className={`${
									currentPage === 1 ? ' text-gray-500 cursor-not-allowed' : ''
								}`}
							>
								{'<<'}
							</p>
							<button
								disabled={currentPage === 1}
								className={`${
									currentPage === 1 ? 'text-gray-500  cursor-not-allowed' : ' text-white'
								} `}
							>
								Previous
							</button>
						</div>

						<div
							className='flex flex-row  items-center text-white text-xs space-x-2 cursor-pointer'
							onClick={() => handlePageChange(currentPage + 1)}
						>
							<button
								disabled={currentPage === totalPages}
								className={`${
									currentPage === totalPages ? ' text-gray-500 cursor-not-allowed' : ''
								}  ml-2`}
							>
								Next
							</button>
							<p
								className={`${
									currentPage === totalPages ? ' text-gray-500 cursor-not-allowed' : ''
								} `}
							>
								{'>>'}
							</p>
						</div>
					</div>
				</div>
			</nav>
		</div>
	)
}

export default CustomTable
