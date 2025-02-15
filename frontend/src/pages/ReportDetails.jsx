/* eslint-disable react/prop-types */
import Header from '../partials/Header'
import Sidebar from '../partials/Sidebar'

import {useParams} from 'react-router-dom'
import StatisticsList from '../components/StatisticsList'
import React, {useContext, useEffect, useState} from 'react'
import axios from 'axios'
import {ThreeDots} from 'react-loader-spinner'
import {Toaster} from 'react-hot-toast'
import {customToast} from '../utils/utils'
import {errorMsgStyle} from '../data/optionsData'
import AnalysisContext from '../contexts/AnalysisContext'
import {reportDetailsColumns as columns} from '../data/optionsData'

const PROD_API_URL = window.PROD_URL_API

const ReportDetails = () => {
    const {reportID} = useParams()
    const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

    const {
        analysis,
        setAnalysis,
        // analysisDetail,
        summary,
        setSummary,
        downloadURL,
        setDownloadURL,
        status,
        setStatus,
        setAnalysisDetail,
    } = useContext(AnalysisContext)

    const [loading, setLoading] = useState(false)
    //
    // useEffect(() => {
    //     setSummary(analysisDetail.summary)
    //     setStatus(analysisDetail.status)
    //     setAnalysis(analysisDetail.analysis)
    // }, [
    //     analysisDetail,
    //     reportID,
    //     status,
    //     summary,
    //     analysis,
    //     setAnalysis,
    //     setSummary,
    //     setStatus,
    // ])
    const downloadFile = () => {
        // Create a temporary link to download the file
        const link = document.createElement('a');
        link.href = downloadURL;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };
    useEffect(() => {
        setAnalysis([])
        setAnalysisDetail({})
        const fetchData = async () => {
            setLoading(true)
            try {
                const response = await axios.get(`${PROD_API_URL}/report?${reportID}`)
                if (response.status === 200) {
                    setStatus(response.data.summary.status)
                    setSummary(response.data.summary)
                    if (response.data.summary.status === 'Error') {
                        customToast('The Analysis Encountered an Error', '❌', errorMsgStyle)
                        setLoading(false)
                    } else if (response.data.summary.status === 'Running') {
                        // console.log('Fetching Data Again')
                        await delay(3000)
                        return await fetchData()
                    } else {
                        setAnalysis(response.data.analysis)
                        setAnalysisDetail(response.data)
                        setDownloadURL(response.data.url)
                        setLoading(false)
                    }

                    return response // Return response if successful
                }
            } catch (error) {
                customToast('Server is not responding', '❌', errorMsgStyle)
                throw error // Throw error on the last attempt
            }
        }

        fetchData()
    }, [reportID, setAnalysis, setSummary, setStatus])

    const reportNumber = reportID.split('=')

    return (
        <div className='flex'>
            <Toaster/>
            <Sidebar/>
            <div className='bg-darkblue w-full h-screen overflow-y-scroll p-10 pt-0 space-y-6 '>
                <Header title='Analysis | Dashboard'></Header>

                <div className='flex flex-col  gap-y-4 lg:gap-y-4 pb-6'>
                    <div
                        className=' text-base flex flex-row  font-semibold text-third-dark items-center   rounded-md  '>
                        <p>Analysis ID : </p>
                        <p className='text-white/70 text-sm ml-4'>{reportNumber[1]}</p>
                    </div>
                    {status === 'Completed' && (
                        <div className='text-sm flex flex-row font-semibold text-lambdaPrimary rounded-md justify-between'>
                            <div className='flex items-center'>
                                <p className='hidden lg:flex'>Analysis Date:</p>
                                <p className='text-white/70 text-sm lg:ml-4'>
                                    {new Date(summary.startDate).toDateString()} - {new Date(summary.endDate).toDateString()}
                                </p>
                            </div>
                            <button onClick={downloadFile} className='ml-auto  bg-lambdaPrimary text-white px-4 py-2 rounded'>
                                Download CSV
                            </button>
                        </div>
                    )}

                </div>

                {status === 'Completed' && analysis.length > 0 ? (
                    <div className='grid grid-cols-2 md:grid-cols-6  gap-x-6 gap-y-10 text-xs'>
                        <StatisticsList summary={summary}/>
                    </div>
                ) : status === 'Running' ? (
                    <div className='text-xs text-yellow-600'>
                        Report is still processing
                    </div>
                ) : (
                    status === 'Error' && (
                        <div className='text-xs text-red-600'> Report generation failed</div>
                    )
                )}
                {loading && (
                    <div className='flex justify-center items-center mt-10'>
                        <ThreeDots
                            visible={true}
                            height='40'
                            width='40'
                            color='#4fa94d'
                            radius='9'
                            ariaLabel='three-dots-loading'
                            wrapperStyle={{}}
                            wrapperClass=''
                        />
                    </div>
                )}

                {status === 'Completed' && (
                    <div className='pt-4'>
                        {' '}
                        <DynamicTable data={analysis}/>{' '}
                    </div>
                )}
            </div>
        </div>
    )
}

const DynamicTable = ({data}) => {
    const [sortConfig, setSortConfig] = useState({
        key: null,
        direction: 'ascending',
    })

    const sortedData = React.useMemo(() => {
        let sortableItems = [...data]
        if (sortConfig !== null) {
            sortableItems.sort((a, b) => {
                if (a[sortConfig.key] < b[sortConfig.key]) {
                    return sortConfig.direction === 'ascending' ? -1 : 1
                }
                if (a[sortConfig.key] > b[sortConfig.key]) {
                    return sortConfig.direction === 'ascending' ? 1 : -1
                }
                return 0
            })
        }
        return sortableItems
    }, [data, sortConfig])

    const requestSort = (key) => {
        let direction = 'ascending'
        if (sortConfig.key === key && sortConfig.direction === 'ascending') {
            direction = 'descending'
        }
        setSortConfig({key, direction})
    }

    return (
        <>
            {data.length !== 0 ? (
                <div className='relative overflow-x-auto shadow-md sm:rounded-md'>
                    <table
                        className='w-full text-sm text-left rtl:text-right text-white border border-darkblueLight rounded-md'>
                        <thead className='text-xs uppercase text-white bg-darkblueLight py-2'>
                        <tr className='px-6 py-3 cursor-pointer '>
                            {columns.map((column) => (
                                <th
                                    key={column.key}
                                    scope='col'
                                    className='px-6 py-3  hover:text-third-dark transition-all duration-300 ease-in-out'
                                    onClick={() => requestSort(column.key)}
                                >
                                    {column.label}
                                </th>
                            ))}
                        </tr>
                        </thead>
                        <tbody>
                        {sortedData.map((row, index) => (
                            <tr
                                key={index}
                                className={`${index % 2 === 0 ? 'bg-darkblueMedium' : 'bg-transparent'} cursor-pointer text-xs hover:bg-green-900/40${row.timeoutInvocations > 0 ? 'text-red-500' : ''} ${row.provisionedMemoryMB > row.optimalMemory * 2 ? 'text-yellow-500' : ''}`}
                            >
                                {columns.map((column) => (
                                    <td key={column.key} className='px-6 py-3'>
                                        {row[column.key]}
                                    </td>
                                ))}
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            ) : (
                <div className='text-gray-400 text-center flex justify-center items-center  text-md mt-10'>
                    Data is not available
                </div>
            )}
        </>
    )
}

export default ReportDetails
